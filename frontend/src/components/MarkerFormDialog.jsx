import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { markerFormSchema } from "@/lib/schemas";
import { ReactTags } from "react-tag-autocomplete";
import { useCallback, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import MapSelector from "./MapSelector";
import { X } from "lucide-react";

const MarkerFormDialog = ({
  isOpen,
  setIsOpen,
  onSave,
  initialData = null,
  mode = "add",
}) => {
  const form = useForm({
    resolver: zodResolver(markerFormSchema),
    defaultValues: initialData || {
      name: "",
      coordinate: {
        latitude: "",
        longitude: "",
      },
      subscribedEmails: [],
    },
  });

  useEffect(() => {
    if (initialData) {
      form.reset({
        name: initialData.name,
        coordinate: {
          latitude: initialData.coordinate.latitude,
          longitude: initialData.coordinate.longitude,
        },
        subscribedEmails: initialData.subscribedEmails || [],
      });
    }
  }, [initialData, form.reset, form]);

  const onSubmit = async (data) => {
    await onSave(data);
    setIsOpen(false);
    form.reset();
  };

  const handleLocationSelect = (coordinates) => {
    form.setValue("coordinate.latitude", coordinates.latitude);
    form.setValue("coordinate.longitude", coordinates.longitude);
  };

  const currentCoordinates = form.watch("coordinate");
  const initialMapLocation =
    currentCoordinates.latitude && currentCoordinates.longitude
      ? {
          lat: parseFloat(currentCoordinates.latitude),
          lng: parseFloat(currentCoordinates.longitude),
        }
      : null;

  const onAdd = useCallback(
    (newTag) => {
      const currentEmails = form.getValues("subscribedEmails") || [];
      form.setValue("subscribedEmails", [...currentEmails, newTag]);
    },
    [form]
  );

  const onDelete = useCallback(
    (tagIndex) => {
      const currentEmails = form.getValues("subscribedEmails") || [];
      form.setValue(
        "subscribedEmails",
        currentEmails.filter((_, i) => i !== tagIndex)
      );
    },
    [form]
  );

  const renderTag = useCallback(
    ({ classNames, tag, removeButtonProps }) => (
      <div className={classNames.tag}>
        <span className={classNames.tagName}>{tag.label}</span>
        <button
          {...removeButtonProps}
          className="react-tags__delete-button"
          aria-label="Remove email"
        >
          <X size={14} />
        </button>
      </div>
    ),
    []
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>
            {mode === "add" ? "Add a new marker" : "Edit marker"}
          </DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Location name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="space-y-2">
              <FormLabel>Location</FormLabel>
              <MapSelector
                onSelectLocation={handleLocationSelect}
                initialLocation={initialMapLocation}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="coordinate.latitude"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Latitude</FormLabel>
                      <FormControl>
                        <Input {...field} readOnly />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="coordinate.longitude"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Longitude</FormLabel>
                      <FormControl>
                        <Input {...field} readOnly />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {mode !== "add" && (
              <FormField
                control={form.control}
                name="subscribedEmails"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Emails</FormLabel>
                    <FormControl>
                      <ReactTags
                        selected={(field.value || []).map((email) => ({
                          label: email,
                          value: email,
                        }))}
                        labelText="Emails"
                        onAdd={(tag) => onAdd(tag.value)}
                        onDelete={onDelete}
                        allowNew={true}
                        newOptionText="Press enter to add: %value%"
                        onValidate={(email) => {
                          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                          return emailRegex.test(email);
                        }}
                        placeholderText="Type email and press enter"
                        noOptionsText="Type a valid email"
                        renderTag={renderTag}
                        classNames={{
                          root: "react-tags",
                          rootIsActive: "is-active",
                          rootIsDisabled: "is-disabled",
                          rootIsInvalid: "is-invalid",
                          label: "react-tags__label",
                          tagList: "react-tags__list",
                          tagListItem: "react-tags__list-item",
                          tag: "react-tags__tag",
                          tagName: "react-tags__tag-name",
                          comboBox: "react-tags__combobox",
                          input: "react-tags__combobox-input",
                          listBox: "react-tags__listbox",
                          option: "react-tags__listbox-option",
                          optionIsActive: "is-active",
                        }}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <Button type="submit" className="w-full">
              {mode === "add" ? "Add Marker" : "Save Changes"}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default MarkerFormDialog;
